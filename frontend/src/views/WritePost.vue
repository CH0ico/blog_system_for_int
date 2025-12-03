<template>
  <div class="write-post">
    <el-card>
      <h2>写文章</h2>

      <el-form :model="form" label-width="90px" @submit.prevent="onSubmit">
        <el-form-item label="标题">
          <el-input v-model="form.title" />
        </el-form-item>

        <el-form-item label="分类">
          <el-select v-model="form.categories" multiple placeholder="选择分类">
            <el-option
              v-for="c in categoryOptions"
              :key="c.id"
              :label="c.name"
              :value="c.name"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="标签">
          <el-select
            v-model="form.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="添加标签"
          >
            <el-option
              v-for="t in tagOptions"
              :key="t.id"
              :label="t.name"
              :value="t.name"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio label="draft">草稿</el-radio>
            <el-radio label="published">发布</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="内容">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="15"
            placeholder="支持 Markdown"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="onSubmit">发布</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/utils/axios'   // 你项目自己的 axios 封装（要带上 token）

const router = useRouter()

const form = reactive({
  title: '',
  content: '',
  summary: '',
  tags: [],
  categories: [],
  status: 'published',
  is_featured: false,
  allow_comments: true,
})

const categoryOptions = reactive([])
const tagOptions = reactive([])

onMounted(async () => {
  // 获取分类
  const catRes = await axios.get('/api/posts/categories')
  // 你的接口返回 { categories: [...] }
  categoryOptions.splice(0, categoryOptions.length, ...catRes.data.categories)

  // 获取标签
  const tagRes = await axios.get('/api/posts/tags')
  tagOptions.splice(0, tagOptions.length, ...tagRes.data.tags)
})

const onSubmit = async () => {
  if (!form.title.trim() || !form.content.trim()) {
    return alert('标题和内容不能为空')
  }

  const payload = {
    ...form,
    summary: form.summary || form.content.slice(0, 200),
  }

  const res = await axios.post('/api/posts/', payload)
  // 成功后跳到新文章详情页
  const post = res.data.post
  router.push({ name: 'PostDetail', params: { post_id: post.id } })
}
</script>

<style scoped>
.write-post {
  max-width: 900px;
  margin: 24px auto;
}
</style>
